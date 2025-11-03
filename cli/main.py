import getpass
from core.recorder import WorkflowRecorder

def main():
    print("="*60)
    print(" ENHANCED UI WORKFLOW RECORDER FRAMEWORK ")
    print("="*60)

    base_url = input("Enter website URL (e.g. https://example.com): ").strip()
    username = input("Username/Email: ").strip()
    password = getpass.getpass("Password: ")

    recorder = WorkflowRecorder(base_url, username, password)
    requests, cookies, token = recorder.record_workflow()

    output = "reports/generated_scripts/load_test.py"
    recorder.generate_locust_script(requests, cookies, token, output)

    print("\n✅ Done! Generated Locust script at:")
    print(output)
    print("\nTo run load test:")
    print(f"  locust -f {output} --host={base_url}")
    print("  Visit http://localhost:8089")

if __name__ == "__main__":
    main()
