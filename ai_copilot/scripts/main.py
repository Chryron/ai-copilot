from ai_copilot.lib.decision import process_input
def main():
    print("Welcome to the AI coding CLI!")
    while True:
        user_input = input("Please enter your query: ")
        result = process_input(user_input)
        print(result)

if __name__ == '__main__':
    main()