from .stock_ui import StockUI
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Trading Bot CLI')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    
    args = parser.parse_args()
    
    try:
        ui = StockUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 