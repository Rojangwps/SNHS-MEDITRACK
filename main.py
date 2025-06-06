import sys
from PyQt5.QtWidgets import QApplication
from dashboard_ui import DashboardUI

def main():
    app = QApplication(sys.argv)
    try:
        dashboard = DashboardUI()
        dashboard.show()
        sys.exit(app.exec_())
    except Exception as e:
        print("Error in main:", e)

if __name__ == "__main__":
    main()
