import subprocess
import sys

interact = [sys.executable, 'aepeash_final.py']
refresh = [sys.executable, 'get_data.py']


def interactive_prompt():
    response = ''

    while response != 'exit':
        response = input("Enter 'interact' to work with the current data"
                         "\nor enter 'refresh' to refresh the database"
                         "\ntype 'exit' to leave the program: "
                         "\n").lower().strip()

        if response == 'exit':
            continue
        elif response == 'interact':
            subprocess.call(interact)

        elif response == 'refresh':
            print('refreshing...')
            subprocess.call(refresh)
        else:
            print('Sorry your command is not recognized')



if __name__ == '__main__':
    interactive_prompt()