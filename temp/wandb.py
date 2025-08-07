class Vehicle:
    def __init__(self, brand: str, fuel_type: str) -> None:
        self.brand = brand
        self.fuel_type = fuel_type

    def shout(self):
        return f"This is a vehicle of brand" + self.brand

bmw: Vehicle = Vehicle(brand="bmw", fuel_type="oil")
print(bmw.shout())


class Car(Vehicle):
    def new_shout():


