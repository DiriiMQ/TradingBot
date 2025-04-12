from .stock_info import StockInfo
import sys

class StockUI:
    def __init__(self):
        self.stock_info = StockInfo()
        self.running = True

    def display_menu(self):
        """Display the main menu"""
        print("\n=== Stock Symbol Manager ===")
        print("1. View Favorite Symbols")
        print("2. View All Available Symbols")
        print("3. Add Symbol")
        print("4. Remove Symbol")
        print("5. Exit")
        print("===========================")

    def view_symbols(self):
        """Display current favorite symbols"""
        symbols = self.stock_info.get_favorite_symbols()
        if not symbols:
            print("\nNo favorite symbols found.")
            return

        print("\nCurrent Favorite Symbols:")
        for i, symbol in enumerate(symbols, 1):
            print(f"{i}. {symbol}")

    def view_all_symbols(self):
        """Display all available symbols"""
        try:
            print("\nFetching all available symbols...")
            all_symbols = self.stock_info._load_all_symbols_by_exchanges()
            
            if not all_symbols:
                print("No symbols found.")
                return

            # Group symbols by exchange
            symbols_by_exchange = {}
            for symbol in all_symbols:
                exchange = symbol.split('.')[-1] if '.' in symbol else 'UNKNOWN'
                if exchange not in symbols_by_exchange:
                    symbols_by_exchange[exchange] = []
                symbols_by_exchange[exchange].append(symbol)

            # Display symbols grouped by exchange
            for exchange, symbols in symbols_by_exchange.items():
                print(f"\n=== {exchange} Exchange ===")
                # Display symbols in columns for better readability
                for i in range(0, len(symbols), 5):
                    print(' '.join(f"{s:<8}" for s in symbols[i:i+5]))
            
            print(f"\nTotal symbols: {len(all_symbols)}")
            
        except Exception as e:
            print(f"\nError fetching symbols: {str(e)}")

    def add_symbol(self):
        """Add a new symbol to favorites"""
        symbol = input("\nEnter symbol to add: ").strip().upper()
        if not symbol:
            print("Symbol cannot be empty.")
            return

        if self.stock_info.add_favorite_symbol(symbol):
            print(f"Successfully added {symbol} to favorites.")
        else:
            print(f"Symbol {symbol} is already in favorites or could not be added.")

    def remove_symbol(self):
        """Remove a symbol from favorites"""
        self.view_symbols()
        symbol = input("\nEnter symbol to remove: ").strip().upper()
        if not symbol:
            print("Symbol cannot be empty.")
            return

        if self.stock_info.remove_favorite_symbol(symbol):
            print(f"Successfully removed {symbol} from favorites.")
        else:
            print(f"Symbol {symbol} was not found in favorites.")

    def run(self):
        """Run the UI loop"""
        while self.running:
            self.display_menu()
            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == '1':
                self.view_symbols()
            elif choice == '2':
                self.view_all_symbols()
            elif choice == '3':
                self.add_symbol()
            elif choice == '4':
                self.remove_symbol()
            elif choice == '5':
                print("\nGoodbye!")
                self.running = False
            else:
                print("\nInvalid choice. Please try again.")

            if self.running:
                input("\nPress Enter to continue...")

def main():
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