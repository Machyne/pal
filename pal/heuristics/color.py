class Colors(object):
    # ex: for underlined green text
    #   print Colors.green + Colors.u_Score + "I'm a String"
    #   print Colors.reset <-- This resets the colors to be the default

    # Colors
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    magenta = "\x1b[35m"
    cyan = "\x1b[36m"
    white = "\x1b[37m"

    # Effects
    blink = "\x1b[5m"
    u_Score = "\x1b[4m"
    reverse = "\x1b[7m"
    normal = "\x1b[0m"
    reset = normal

if __name__ == '__main__':
    main()
