#!/usr/bin/env python
import host

def main():
    iter = range(10).__iter__()
    while iter:
        print(iter)
        iter.next()
    
if __name__ == '__main__':
    main()
