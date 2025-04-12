from .stock_info import StockInfo
import sys
import pandas as pd

class StockUI:
    def __init__(self):
        self.stock_info = StockInfo()
        self.running = True

    def display_menu(self):
        """Display the main menu"""
        print("\n=== Stock Symbol Manager ===")
        print("1. View Favorite Symbols")
        print("2. View All Available Symbols")
        print("3. View Available Groups")
        print("4. View Symbols in Group")
        print("5. Add Symbol")
        print("6. Remove Symbol")
        print("7. Exit")
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
            all_symbols_df = self.stock_info._load_all_symbols_by_exchanges()
            
            if all_symbols_df.empty:
                print("No symbols found.")
                return

            # Group symbols by exchange
            symbols_by_exchange = {}
            for _, row in all_symbols_df.iterrows():
                exchange = row['exchange']
                if exchange not in symbols_by_exchange:
                    symbols_by_exchange[exchange] = []
                symbols_by_exchange[exchange].append({
                    'symbol': row['symbol'],
                    'type': row['type'],
                    'name': row['organ_short_name']
                })

            # Display symbols grouped by exchange
            for exchange in self.stock_info.VN_EXCHANGES:
                if exchange in symbols_by_exchange:
                    symbols = symbols_by_exchange[exchange]
                    print(f"\n=== {exchange} Exchange ({len(symbols)} symbols) ===")
                    # Sort symbols alphabetically
                    symbols.sort(key=lambda x: x['symbol'])
                    
                    # Display symbols in a formatted table
                    print(f"{'Symbol':<8} {'Type':<10} {'Company Name'}")
                    print("-" * 60)
                    for symbol_info in symbols:
                        print(f"{symbol_info['symbol']:<8} {symbol_info['type']:<10} {symbol_info['name']}")
            
            print(f"\nTotal symbols: {len(all_symbols_df)}")
            
        except Exception as e:
            print(f"\nError fetching symbols: {str(e)}")

    def view_available_groups(self):
        """Display all available groups"""
        try:
            groups = self.stock_info.get_all_available_groups()
            if not groups:
                print("\nNo groups found.")
                return

            print("\nAvailable Groups:")
            for i, group in enumerate(groups, 1):
                print(f"{i}. {group}")
            
        except Exception as e:
            print(f"\nError fetching groups: {str(e)}")

    def view_symbols_in_group(self):
        """Display symbols in a specific group"""
        try:
            # First show available groups
            self.view_available_groups()
            
            group = input("\nEnter group name: ").strip().upper()
            if not group:
                print("Group name cannot be empty.")
                return

            print(f"\nFetching symbols in group {group}...")
            symbols_data = self.stock_info.get_formatted_symbols_by_group(group)
            
            if not symbols_data:
                print(f"No symbols found in group {group}.")
                return

            # Display symbols in a formatted table
            print(f"\n=== Symbols in {group} Group ===")
            print(f"{'Symbol':<8} {'Type':<10} {'Organization':<30}")
            print("-" * 50)
            for symbol_info in symbols_data:
                print(f"{symbol_info['symbol']:<8} {symbol_info['type']:<10} {symbol_info['organ_short_name']:<30}")
        
            print(f"\nTotal symbols in {group}: {len(symbols_data)}")
            
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
            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == '1':
                self.view_symbols()
            elif choice == '2':
                self.view_all_symbols()
            elif choice == '3':
                self.view_available_groups()
            elif choice == '4':
                self.view_symbols_in_group()
            elif choice == '5':
                self.add_symbol()
            elif choice == '6':
                self.remove_symbol()
            elif choice == '7':
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