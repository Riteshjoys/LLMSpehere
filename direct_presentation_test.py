#!/usr/bin/env python3

import sys
import asyncio
import traceback
sys.path.append('/app/backend')

async def test_presentation_methods():
    """Test the presentation service methods directly to identify exact issues"""
    
    print("=== DIRECT PRESENTATION SERVICE TESTING ===")
    
    try:
        from services.presentation_service import PresentationService
        from utils.database import get_database
        
        service = PresentationService()
        db = get_database()
        test_user_id = "test_user_123"
        
        print("✅ Successfully imported presentation service")
        
        # Test 1: get_presentation_history
        print("\n1. Testing get_presentation_history...")
        try:
            history = await service.get_presentation_history(db, test_user_id)
            print(f"✅ SUCCESS: get_presentation_history returned {len(history)} items")
        except Exception as e:
            print(f"❌ FAILED: get_presentation_history - {str(e)}")
            traceback.print_exc()
        
        # Test 2: get_presentation_stats
        print("\n2. Testing get_presentation_stats...")
        try:
            stats = await service.get_presentation_stats(db, test_user_id)
            print(f"✅ SUCCESS: get_presentation_stats returned {stats}")
        except Exception as e:
            print(f"❌ FAILED: get_presentation_stats - {str(e)}")
            traceback.print_exc()
        
        # Test 3: Create a test presentation for export testing
        print("\n3. Creating test presentation for export testing...")
        try:
            presentation_id = await service.create_presentation(
                db, 
                template_id="business_pitch",
                title="Test Export Presentation",
                data={"test": "export_data"},
                user_id=test_user_id
            )
            print(f"✅ SUCCESS: Created test presentation {presentation_id}")
            
            # Get the presentation for export testing
            presentation = await service.get_presentation(db, presentation_id)
            print(f"✅ Retrieved presentation: {presentation['title'] if presentation else 'None'}")
            
            if presentation:
                # Test 4: Export to PPTX
                print("\n4. Testing export to PPTX...")
                try:
                    pptx_data = await service._export_to_pptx(presentation)
                    print(f"✅ SUCCESS: PPTX export returned {len(pptx_data)} bytes")
                except Exception as e:
                    print(f"❌ FAILED: PPTX export - {str(e)}")
                    traceback.print_exc()
                
                # Test 5: Export to PDF
                print("\n5. Testing export to PDF...")
                try:
                    pdf_data = await service._export_to_pdf(presentation)
                    print(f"✅ SUCCESS: PDF export returned {len(pdf_data)} bytes")
                except Exception as e:
                    print(f"❌ FAILED: PDF export - {str(e)}")
                    traceback.print_exc()
                
                # Test 6: Export to Google Slides
                print("\n6. Testing export to Google Slides...")
                try:
                    gs_data = await service._export_to_google_slides(presentation)
                    print(f"✅ SUCCESS: Google Slides export returned {gs_data}")
                except Exception as e:
                    print(f"❌ FAILED: Google Slides export - {str(e)}")
                    traceback.print_exc()
            
        except Exception as e:
            print(f"❌ FAILED: Could not create test presentation - {str(e)}")
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ FAILED: Could not import presentation service - {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_presentation_methods())