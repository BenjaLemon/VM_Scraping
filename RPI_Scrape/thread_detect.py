import psutil

def Write(thread_count):
    print('\nWriting data to thread_count.txt')
    with open('thread_count.txt', 'w') as f:
        f.write(f'{thread_count}')
    print('Done')


print('Detecting number of logical CPUs (Cores*Threads/core)')
thread_count = psutil.cpu_count()



push = None
while push not in ['y','n']:
    if thread_count is None:
        print('Failed to read Logical cores, defaulting to Thread number=1')
        Write(1)
        break
    else: 
        push = str(input(f'\n Thread number={thread_count}, push to txt file (y/n)?'))
        if push == 'y':
            Write(thread_count)
        elif push == 'n':
            print(f'Nothing to do, code exiting')
        else:
            print('{push} not a valid option, please enter y/n')


