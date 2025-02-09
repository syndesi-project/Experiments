from syndesi_drivers.multimeters.siglent_sdm30x5 import SDM3055

def main():
    mm = SDM3055('192.168.1.201')


    print(f"Identification : {mm.get_identification}")


if __name__ == '__main__':
    main()