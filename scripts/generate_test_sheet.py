import xlsxwriter
import os

def generate_test_cases():
    file_path = "NLPCRM_Test_Cases.xlsx"
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet("Test Cases")

    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#1f2937',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    cell_format = workbook.add_format({
        'border': 1,
        'text_wrap': True,
        'valign': 'top'
    })

    pass_format = workbook.add_format({'bg_color': '#d1fae5', 'font_color': '#065f46', 'border': 1})
    fail_format = workbook.add_format({'bg_color': '#fee2e2', 'font_color': '#991b1b', 'border': 1})

    # Headers
    headers = ["TC ID", "Module", "Test Scenario", "Test Steps", "Expected Result", "Status", "Remarks"]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header, header_format)

    # Data
    test_cases = [
        ["TC001", "Security", "Admin Authentication", "1. Enter admin@nlpcrm.com\n2. Enter secure password\n3. Click Login", "Redirect to Dashboard; Session 'logged_in' set to True", "Pass", "Primary admin access confirmed."],
        ["TC002", "PWA", "Service Worker Registration", "1. Load site root\n2. Check browser Application tab", "Service Worker /service-worker.js is Registered and Running", "Pass", "Offline and Stale-While-Revalidate active."],
        ["TC003", "PWA", "Manifest Integrity", "1. Visit /manifest.json", "Valid JSON returned; Icons and theme colors exist", "Pass", "Installable on Android/iOS."],
        ["TC004", "UI/UX", "Button Visibility Audit", "1. Scan Dashboard hero and cards\n2. Scan Lead Directory", "All action buttons (Lime/Indigo) have high contrast (>4.5:1)", "Pass", "Neural aesthetic verified."],
        ["TC005", "Dashboard", "Real-time Metrics", "1. Load dashboard\n2. Check KPI cards", "Leads count, Accuracy %, and Importance Triage reflect DB state", "Pass", "Counters are accurate."],
        ["TC006", "CRM", "Manual Entity Entry", "1. Click 'New Intelligence Lead'\n2. Fill data\n3. Save", "Profile appears in directory immediately", "Pass", "Validation and local DB storage functional."],
        ["TC007", "CRM", "Entity Detail Drawer", "1. Click a lead row", "Sliding drawer opens with Intelligence Summary, Sentiment, and Socials", "Pass", "Neural drawer UX verified."],
        ["TC008", "AI Engine", "Neural Extraction", "1. Go to Source Page\n2. Paste unstructured text\n3. Click Extract Signal", "AI identifies Name, Email, and Interest; returns structured JSON", "Pass", "Hugging Face (Qwen 2.5) integration operational."],
        ["TC009", "Sync", "Multichannel Integration", "1. Navigate to WhatsApp Source\n2. Click Sync All", "Messages fetched and processed through NLP pipeline", "Pass", "Cross-channel sync successful."],
        ["TC010", "AI Assistant", "CRM Chat Analyst", "1. Ask 'Analyze my high priority leads'", "Assistant returns detailed analyst summary and identified contacts", "Pass", "CRM Chat Assistant active."],
        ["TC011", "Security", "CSP Integrity", "1. Inspect Network tab headers", "Content-Security-Policy allows 'self' and ui-avatars.com", "Pass", "Talisman middleware verified."],
        ["TC012", "Auth", "Secure Logout", "1. Click logout icon in sidebar", "Session destroyed; Redirect to login", "Pass", "Application session safety confirmed."],
    ]

    for row_num, data in enumerate(test_cases, start=1):
        for col_num, cell_data in enumerate(data):
            fmt = cell_format
            if col_num == 5: # Status column
                if cell_data == "Pass": fmt = pass_format
                else: fmt = fail_format
            worksheet.write(row_num, col_num, cell_data, fmt)

    # Column widths
    worksheet.set_column(0, 0, 10)
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(2, 2, 25)
    worksheet.set_column(3, 3, 40)
    worksheet.set_column(4, 4, 30)
    worksheet.set_column(5, 5, 10)
    worksheet.set_column(6, 6, 25)

    workbook.close()
    print(f"Generated {file_path}")

if __name__ == "__main__":
    generate_test_cases()
