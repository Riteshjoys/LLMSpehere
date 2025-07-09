def run_all_tests():
    print("\n" + "=" * 80)
    print("STARTING CONTENTFORGE AI BACKEND API TESTS")
    print("=" * 80)
    
    # Run tests in sequence
    health_check_success = test_health_check()
    registration_success = test_user_registration()
    login_success = test_user_login()
    get_user_success = test_get_current_user()
    provider_management_success = test_admin_provider_management()
    provider_from_curl_success = test_admin_provider_from_curl()
    public_provider_success = test_public_provider_routes()
    text_generation_success = test_text_generation()
    image_generation_success = test_image_generation()
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_tests_passed = all([
        health_check_success,
        registration_success,
        login_success,
        get_user_success,
        provider_management_success,
        provider_from_curl_success,
        public_provider_success,
        text_generation_success,
        image_generation_success
    ])
    
    for test_name, result in test_results.items():
        if isinstance(result, dict) and "success" in result:
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            print(f"{status} - {test_name}")
    
    print("\n" + "=" * 80)
    print(f"OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_tests_passed else '❌ SOME TESTS FAILED'}")
    print("=" * 80)
    
    return all_tests_passed
