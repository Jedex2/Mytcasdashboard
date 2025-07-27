import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

class EnhancedTCASScraper:
    def __init__(self):
        self.programs_data = []
        self.base_url = "https://course.mytcas.com"

    async def search_and_collect_programs(self, page, keyword):
        """ค้นหาและรวบรวมหลักสูตร - ใช้วิธีที่เฉพาะเจาะจง"""
        programs = []
        
        try:
            print(f"\n🔍 ค้นหา: {keyword}")
            
            # ไปหน้าหลัก
            await page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(2000)
            
            # ใช้ selector ที่เฉพาะเจาะจงตามตัวอย่าง
            search_selectors = [
                "input[placeholder='พิมพ์ชื่อมหาวิทยาลัย คณะ หรือหลักสูตร']",
                "input[placeholder*='ค้นหา']",
                "input[type='search']",
                "input.search-input",
                "#search-input"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = await page.wait_for_selector(selector, timeout=5000)
                    if search_input:
                        print(f"  ✅ พบช่องค้นหา: {selector}")
                        break
                except:
                    continue
            
            if not search_input:
                print("❌ ไม่พบช่องค้นหา")
                return []
            
            # ทำการค้นหา
            await search_input.fill("")
            await page.wait_for_timeout(500)
            await search_input.fill(keyword)
            await search_input.press("Enter")
            await page.wait_for_timeout(3000)
            
            # หาผลลัพธ์ด้วย selector หลายแบบ
            result_selectors = [
                ".t-programs > li",
                ".program-list li",
                ".search-results li",
                ".results li",
                "[data-testid='program-item']"
            ]
            
            results = []
            for selector in result_selectors:
                try:
                    results = await page.query_selector_all(selector)
                    if results:
                        print(f"  ✅ พบผลลัพธ์: {selector} ({len(results)} รายการ)")
                        break
                except:
                    continue
            
            if not results:
                print("  ❌ ไม่พบผลลัพธ์")
                return []
            
            # ประมวลผลรายการที่พบ
            for i, li in enumerate(results):
                try:
                    # ดึงข้อมูลพื้นฐาน
                    title_full = await li.inner_text()
                    
                    # หาลิงก์
                    link_element = await li.query_selector("a")
                    if not link_element:
                        continue
                        
                    link = await link_element.get_attribute("href")
                    full_link = link if link.startswith("http") else f"{self.base_url}{link}"
                    
                    # แยกข้อมูลจาก title
                    lines = [line.strip() for line in title_full.strip().splitlines() if line.strip()]
                    
                    program_name = lines[0] if len(lines) >= 1 else ""
                    faculty = lines[1].replace('›', ' > ') if len(lines) >= 2 else ""
                    university = lines[2] if len(lines) >= 3 else ""
                    
                    programs.append({
                        'keyword': keyword,
                        'program_name': program_name,
                        'university': university,
                        'faculty': faculty,
                        'title_full': title_full,
                        'url': full_link
                    })
                    
                    print(f"  📌 {i+1:2d}. {program_name[:40]}...")
                    
                except Exception as e:
                    print(f"  ❌ ข้อผิดพลาดในรายการที่ {i+1}: {str(e)}")
                    continue
            
            return programs
            
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการค้นหา {keyword}: {str(e)}")
            return []

    async def scrape_program_details(self, page, program_info):
        """ดึงข้อมูลรายละเอียดจากหน้าของแต่ละโปรแกรม"""
        url = program_info['url']
        
        try:
            print(f"📄 กำลังดึง: {program_info['program_name'][:50]}...")
            
            # เข้าหน้ารายละเอียด
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(2000)
            
            # สร้างข้อมูลพื้นฐาน
            data = {
                'คำค้น': program_info['keyword'],
                'ชื่อหลักสูตร': program_info['program_name'],
                'มหาวิทยาลัย': program_info['university'],
                'คณะ': program_info['faculty'],
                'ประเภทหลักสูตร': 'ไม่พบข้อมูล',
                'ค่าใช้จ่าย': 'ไม่พบข้อมูล',
                'ลิงก์': url,
                'วันที่เก็บข้อมูล': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # ดึงข้อมูลรายละเอียดด้วย selector ที่เฉพาะเจาะจง
            detail_selectors = {
                'ประเภทหลักสูตร': [
                    "dt:has-text('ประเภทหลักสูตร') + dd",
                    "td:has-text('ประเภทหลักสูตร') + td",
                    ".program-type",
                    "[data-field='program_type']"
                ],
                'ค่าใช้จ่าย': [
                    "dt:has-text('ค่าใช้จ่าย') + dd",
                    "dt:has-text('ค่าธรรมเนียม') + dd",
                    "td:has-text('ค่าใช้จ่าย') + td",
                    ".fee-info",
                    ".tuition-fee",
                    "[data-field='fee']"
                ]
            }
            
            # ลองดึงข้อมูลแต่ละฟิลด์
            for field, selectors in detail_selectors.items():
                for selector in selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            text = await element.inner_text()
                            if text.strip():
                                data[field] = text.strip()
                                break
                    except:
                        continue
            
            # ดึงข้อมูลเพิ่มเติมจากตาราง (หากมี)
            try:
                table_rows = await page.query_selector_all("table tr")
                for row in table_rows:
                    cells = await row.query_selector_all("td, th")
                    if len(cells) >= 2:
                        header = await cells[0].inner_text()
                        value = await cells[1].inner_text()
                        
                        if "ประเภท" in header and data['ประเภทหลักสูตร'] == 'ไม่พบข้อมูล':
                            data['ประเภทหลักสูตร'] = value.strip()
                        elif any(word in header for word in ['ค่าใช้จ่าย', 'ธรรมเนียม', 'ค่าเรียน']) and data['ค่าใช้จ่าย'] == 'ไม่พบข้อมูล':
                            data['ค่าใช้จ่าย'] = value.strip()
            except:
                pass
            
            print(f"   ✅ {data['มหาวิทยาลัย'][:25]} - {data['ค่าใช้จ่าย'][:30]}...")
            return data
            
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {str(e)}")
            return None

    async def run_scraping(self, keywords=None):
        """เรียกใช้การ scraping"""
        if keywords is None:
            keywords = ["วิศวกรรม ปัญญาประดิษฐ์", "วิศวกรรม คอมพิวเตอร์"]
        
        print("🚀 เริ่ม Enhanced TCAS Scraper")
        print("="*70)
        print("🔧 ปรับปรุงตามตัวอย่าง:")
        print("   ✅ ใช้ selector ที่เฉพาะเจาะจง")
        print("   ✅ เข้าไปดึงข้อมูลรายละเอียดจากหน้าแต่ละโปรแกรม")
        print("   ✅ ใช้โครงสร้าง HTML แทน regex")
        print("   ✅ มี fallback selector หลายตัว")
        print("="*70)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                locale='th-TH',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()
            
            try:
                all_programs = []
                
                # ขั้นตอนที่ 1: รวบรวมลิงก์ทั้งหมด
                for keyword in keywords:
                    programs = await self.search_and_collect_programs(page, keyword)
                    all_programs.extend(programs)
                    await asyncio.sleep(2)
                
                if not all_programs:
                    print("❌ ไม่พบหลักสูตรใดๆ")
                    return 0
                
                print(f"\n📋 เริ่มดึงข้อมูลรายละเอียด {len(all_programs)} หลักสูตร...")
                
                # ขั้นตอนที่ 2: ดึงข้อมูลรายละเอียดแต่ละหลักสูตร
                for i, program_info in enumerate(all_programs, 1):
                    print(f"\n[{i:2d}/{len(all_programs)}]", end=" ")
                    
                    data = await self.scrape_program_details(page, program_info)
                    if data:
                        self.programs_data.append(data)
                    
                    # หน่วงเวลาป้องกัน rate limiting
                    await asyncio.sleep(1.5)
                
            finally:
                await browser.close()
        
        return len(self.programs_data)

    def save_to_excel(self, filename='enhanced_tcas_data'):
        """บันทึกเป็น Excel"""
        if not self.programs_data:
            print("❌ ไม่มีข้อมูลที่จะบันทึก")
            return None
        
        df = pd.DataFrame(self.programs_data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename}_{timestamp}.xlsx"
        
        # บันทึกเป็น Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        
        print(f"\n💾 บันทึกเรียบร้อย: {filename}")
        print(f"📊 จำนวนข้อมูล: {len(df)} รายการ")
        
        # แสดงสรุป
        if len(df) > 0:
            print(f"\n📈 สรุปตามคำค้น:")
            keyword_counts = df['คำค้น'].value_counts()
            for keyword, count in keyword_counts.items():
                emoji = "🤖" if "ปัญญาประดิษฐ์" in keyword else "💻"
                print(f"   {emoji} {keyword}: {count} รายการ")
            
            # นับที่มีค่าใช้จ่าย
            with_fee = len(df[df['ค่าใช้จ่าย'] != 'ไม่พบข้อมูล'])
            print(f"\n💰 มีข้อมูลค่าใช้จ่าย: {with_fee}/{len(df)} รายการ")
            
            # แสดงตัวอย่างข้อมูล
            print(f"\n📋 ตัวอย่างข้อมูล:")
            for i, row in df.head(3).iterrows():
                print(f"   {i+1}. {row['ชื่อหลักสูตร'][:40]}...")
                print(f"      🏫 {row['มหาวิทยาลัย']}")
                print(f"      💰 {row['ค่าใช้จ่าย']}")
        
        return df

    def save_to_csv(self, filename='enhanced_tcas_data'):
        """บันทึกเป็น CSV สำรอง"""
        if not self.programs_data:
            return None
        
        df = pd.DataFrame(self.programs_data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename}_{timestamp}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 บันทึก CSV สำรอง: {filename}")
        return df

async def main():
    """ฟังก์ชันหลัก"""
    print("🎯 Enhanced TCAS Scraper")
    print("📚 ปรับปรุงจากตัวอย่างที่ให้มา")
    print("="*50)
    
    # ให้ผู้ใช้เลือกคำค้นหา
    print("🔍 เลือกคำค้นหา:")
    print("1. วิศวกรรม ปัญญาประดิษฐ์")
    print("2. วิศวกรรม คอมพิวเตอร์")
    print("3. ทั้งสองคำ")
    print("4. กำหนดเอง")
    
    choice = input("เลือก (1-4): ").strip()
    
    keywords = []
    if choice == "1":
        keywords = ["วิศวกรรม ปัญญาประดิษฐ์"]
    elif choice == "2":
        keywords = ["วิศวกรรม คอมพิวเตอร์"]
    elif choice == "3":
        keywords = ["วิศวกรรม ปัญญาประดิษฐ์", "วิศวกรรม คอมพิวเตอร์"]
    elif choice == "4":
        custom_keywords = input("กรอกคำค้นหา (คั่นด้วยเครื่องหมายจุลภาค): ")
        keywords = [k.strip() for k in custom_keywords.split(',') if k.strip()]
    else:
        keywords = ["วิศวกรรม ปัญญาประดิษฐ์"]
    
    print(f"🎯 จะค้นหา: {', '.join(keywords)}")
    print("="*50)
    
    scraper = EnhancedTCASScraper()
    
    try:
        # เริ่มการ scraping
        found_count = await scraper.run_scraping(keywords)
        
        if found_count > 0:
            print(f"\n🎉 เสร็จสิ้น! ดึงข้อมูลได้ {found_count} หลักสูตร")
            
            # บันทึกข้อมูล
            df = scraper.save_to_excel()
            scraper.save_to_csv()  # สำรอง
            
            print("\n✅ ไฟล์พร้อมใช้งาน!")
            
            if df is not None and len(df) > 0:
                print(f"\n📊 สถิติรวม:")
                print(f"   📚 จำนวนหลักสูตรทั้งหมด: {len(df)}")
                print(f"   🏫 จำนวนมหาวิทยาลัย: {df['มหาวิทยาลัย'].nunique()}")
                print(f"   💰 มีข้อมูลค่าใช้จ่าย: {len(df[df['ค่าใช้จ่าย'] != 'ไม่พบข้อมูล'])}")
        else:
            print("\n❌ ไม่มีข้อมูลที่ดึงได้")
    
    except KeyboardInterrupt:
        print("\n⏹️ หยุดการทำงานโดยผู้ใช้")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {str(e)}")
        import traceback
        print(f"📋 รายละเอียด: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())