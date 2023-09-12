def main():
    f = open("my.txt", "r")

    ret = f.readline()
    while ret:
        print(ret)
        ret = f.readline()
    f.close()

if __name__ == "__main__":
    main()