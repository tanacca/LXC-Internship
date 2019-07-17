import os


def menuLayout(menu, uri):
    while(True):
        os.system("clear")
        print(" ")                                              # blank space
        print(f" Hostname: XXXX         URI: {uri}")            # menu general info
        print("=" * 80)                                         # bound
        print(f" {menu.title}")                                 # menu title
        print(f"-----+{'-'*74}")                                # bound
        i = 0
        for option in menu.options[1:]:                         # menu options
            i += 1
            print(f" [{i}] | {option}")
        print(f"-----+{'-'*74}")                                # bound
        print(f" [0] | {menu.options[0]}")                      # last option (exit/return)
        print("=" * 80)                                           # bottom bound
        answer = input(f" {menu.ask}")                          # question:
        goodAnswers = list(map(str, range(len(menu.options))))  # list od str of good answers ['0', '1', '2', etc...]
        if answer not in goodAnswers:
            print("\n You must only select either ", end='')
            print(*goodAnswers[1:], sep=', ', end='')
            print(" or 0.\n Please press enter to try again...")
            input()
        else:
            return answer
