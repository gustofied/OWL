import rerun as rr

def main():
    print("Hello World")
    rr.init("hey", spawn=True)
    rr.log("hey")
    
    
if __name__ == "__main__":
    main()