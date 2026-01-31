import numpy
import pandas
from datetime import datetime, timedelta

SEED = 42
ANZAHL_KUNDEN = 200
ANZAHL_PRODUKTE = 20
ANZAHL_BESTELLUNGEN = 5000
ANZAHL_MASCHINEN = 10
ANZAHL_SENSORZEILEN = 80000
ANZAHL_TESTS = 200

START_DATUM = "2020-01-01"
ENDE_DATUM = "2025-12-31"

OUT_DIR = "./data"

def create_ids(prefix: str, numbers: int, length: int = 6):
    return [f"{prefix}{i:0{length}d}" for i in range (1, numbers + 1)]

def create_random_dates(numbers: int, start: str, end: str):
    start_date = pandas.to_datetime(start)
    end_date = pandas.to_datetime(end)
    delta_seconds = int((end_date - start_date).total_seconds())
    random_seconds = numpy.random.randint(0, delta_seconds, size = numbers)

    return start_date + pandas.to_timedelta(random_seconds, unit="s")

def checkAndCreate_dir(path: str):
    import os
    os.makedirs(path, exist_ok=True)

def generate():
    numpy.random.seed(SEED)
    checkAndCreate_dir(OUT_DIR)

    #products = create_products()
    #orders = create_orders_for(products)

    #save_rawdata(create_customers(), "customers")
    #save_rawdata(orders, "orders")
    #save_rawdata(products, "products")
    #save_rawdata(create_machines(), "machines")
    #save_rawdata(create_sensorData(), "sensorData")
    save_rawdata(create_sensorData(), "historycSensorData")
    #save_rawdata(create_testresults(products), "testData")

def create_customers():
    customer_ids = create_ids("CUS", ANZAHL_KUNDEN)
    names = ["Gebr. Schmidt ", "Schmidt ","Müllersheim ", "Apfel ", "Birne ", "Banane ", "Rosinen ", "Eiche ", "Birkenbaum ", "Plastik ", "Metall ", "Bau ", "Baufirma ", "RENSt ", "Reste ", "Blumen ", "Blau "]
    organizations = ["GmbH", "AG", "KG", "Gbr", "OHG", "UG", "eG", "GmbH & Co. KG"]
    regions = ["DACH", "BENELUX", "Baltikum", "Balkan", "Grande Region", "Skandinavien"]

    df_kunden = pandas.DataFrame({
        "id": customer_ids,
        "name": numpy.random.choice(names, size = ANZAHL_KUNDEN) + numpy.random.choice(organizations, size = ANZAHL_KUNDEN),
        "region": numpy.random.choice(regions, size = ANZAHL_KUNDEN),
        "hasServiceContract": numpy.random.choice([0, 1], size = ANZAHL_KUNDEN, p= [0.45, 0.55]),
    })

    return df_kunden

def create_products():
    product_ids = create_ids("PROD", ANZAHL_PRODUKTE)
    product_lines = ["Pump-It", "Pump-It Pro", "Wasserpumpe 2000", "Wasserpumpe 4000", "Tauchpumpe 1l", "Tauchpumpe 10l", "Saustark Pumpe XXL", "XS Allzweckpumpe", "XS Allzweckpumpe CareLine", "XS Allzweckpumpe Allrounder", "Tauchpumpe entenfreundlich", "Dreckwasser Industriepumpe 9000"]
    price_class = ["Low-End", "Premium", "Highclass", "Standard"]

    df_products = pandas.DataFrame({
        "id": product_ids,
        "productLine": numpy.random.choice(product_lines, size = ANZAHL_PRODUKTE),
        "priceClass": numpy.random.choice(price_class, size = ANZAHL_PRODUKTE, p=[0.30, 0.40, 0.20, 0.10]),
    })

    return df_products

def create_orders_for(products: pandas.DataFrame):
    order_ids = create_ids("ORD", ANZAHL_BESTELLUNGEN)
    order_dates = create_random_dates(ANZAHL_BESTELLUNGEN, START_DATUM, ENDE_DATUM)
    order_channels = ["Interner Vertrieb", "Partner A", "Partner B", "Partner C", "Partner D", "Partner E", "Partner F", "Onlineshop", "Messe"]

    price_mapping = {}
    for _, row in products.iterrows():
        if row["priceClass"] == "Low-End":
            base = numpy.random.uniform(200, 320)
        elif row ["priceClass"] == "Standard":
            base = numpy.random.uniform(320, 550)
        elif row ["priceClass"] == "Premium":
            base = numpy.random.uniform(550, 1100)
        else:
            base = numpy.random.uniform(1100, 3000)
        price_mapping[row["id"]] = base

    product_ids = create_ids("PROD", ANZAHL_PRODUKTE)
    customer_ids = create_ids("CUS", ANZAHL_KUNDEN)

    products_for_orders = numpy.random.choice(product_ids, ANZAHL_BESTELLUNGEN)
    unit_price = numpy.array([price_mapping[p] for p in products_for_orders])
    quantaty = numpy.random.randint(1, 12, ANZAHL_BESTELLUNGEN)
    discount = numpy.clip(numpy.random.normal(loc = 0.08, scale = 0.05, size = ANZAHL_BESTELLUNGEN), 0, 0.35)

    df_orders = pandas.DataFrame({
        "id": order_ids,
        "date": order_dates,
        "customerId": numpy.random.choice(customer_ids, size = ANZAHL_BESTELLUNGEN),
        "productId": products_for_orders,
        "orderChannel": numpy.random.choice(order_channels, size = ANZAHL_BESTELLUNGEN, p = [0.128016, 0.097082, 0.179659, 0.186855, 0.090701, 0.023917, 0.022478, 0.083629, 0.187663]),
        "quantaty": quantaty,
        "unitPrice": numpy.round(unit_price, 2),
        "discount": numpy.round(discount, 3),
    })

    df_orders["totalPrice"] = numpy.round(
        df_orders["unitPrice"] * df_orders["quantaty"] * (1 - df_orders["discount"]), 2
    )

    return df_orders

def create_machines():
    machine_ids = create_ids("MACH", ANZAHL_MASCHINEN)
    werke = ["Nord", "Süd"]

    df_machine = pandas.DataFrame({
        "id": machine_ids,
        "werk": numpy.random.choice(werke, ANZAHL_MASCHINEN),
    })

    return df_machine

def create_sensorData():
    machine_ids = create_ids("MACH", ANZAHL_MASCHINEN)

    sensor_timestamp = create_random_dates(ANZAHL_SENSORZEILEN, START_DATUM, ENDE_DATUM)
    machine_for_row = numpy.random.choice(machine_ids, size = ANZAHL_SENSORZEILEN)
    temprature = numpy.random.normal(loc = 55, scale = 4, size = ANZAHL_SENSORZEILEN)
    vibration = 2.0 + 0.06 * (temprature - 55) + numpy.random.normal(loc = 0, scale = 0.2, size = ANZAHL_SENSORZEILEN)
    pressure = numpy.random.normal(loc = 8.5, scale = 0.6, size = ANZAHL_SENSORZEILEN)

    df_sensorData = pandas.DataFrame({
        "date": sensor_timestamp,
        "machineId": machine_for_row,
        "temprature": numpy.round(temprature, 2),
        "vibration": numpy.round(vibration, 3),
        "pressure": numpy.round(pressure, 2),
    })

    outlier_rate = 0.005
    k = int(len(df_sensorData) * outlier_rate)
    outlier_idx = numpy.random.choice(df_sensorData.index, size=k, replace=False)
    df_sensorData.loc[outlier_idx, "temprature"] += numpy.random.uniform(20, 35, size=k)
    df_sensorData.loc[outlier_idx, "vibration"] += numpy.random.uniform(2.5, 5.0, size=k)

    return df_sensorData

def create_testresults(products: pandas.DataFrame):
    test_ids = create_ids("TEST", ANZAHL_TESTS)
    product_ids = create_ids("PROD", ANZAHL_PRODUKTE)
    tested_product_ids = numpy.random.choice(product_ids, ANZAHL_TESTS)
    product_charge_number = create_ids("CHARGE", ANZAHL_TESTS)
    test_date = create_random_dates(ANZAHL_TESTS, START_DATUM, ENDE_DATUM)

    rates = {
        "Pump-It": 0.5,
        "XS Allzweckpumpe": 0.5,
        "XS Allzweckpumpe Careline": 0.5,
        "XS Allzweckpumpe Allrounder": 0.5,

        "Pump-It Pro": 1.0,
        "Wasserpumpe 2000": 1.0,
        "Tauchpumpe 1l": 1.0,
        "Tauchpumpe entenfreundlich": 1.0,

        "Wasserpumpe 4000": 10.0,
        "Tauchpumpe 10l": 10.0,
        "Saustark Pumpe XXL": 10.0,
    }

    should_rate_mapping = {}
    for _, row in products.iterrows():
        should_rate_mapping[row["id"]] = rates.get(row["productLine"], 100.0)

    should_rates = numpy.array([should_rate_mapping[p] for p in tested_product_ids])

    rate_ranges = {
        "Pump-It": (0.495, 0.505),
        "XS Allzweckpumpe": (0.495, 0.505),
        "XS Allzweckpumpe Careline": (0.495, 0.505),
        "XS Allzweckpumpe Allrounder": (0.495, 0.505),

        "Pump-It Pro": (0.995, 1.005),
        "Wasserpumpe 2000": (0.995, 1.005),
        "Tauchpumpe 1l": (0.995, 1.005),
        "Tauchpumpe entenfreundlich": (0.995, 1.005),

        "Wasserpumpe 4000": (9.950, 10.050),
        "Tauchpumpe 10l": (9.950, 10.050),
        "Saustark Pumpe XXL": (9.950, 10.050),
}

    default_range = (99.500, 100.500)

    current_rate_mapping = {}
    for _, row in products.iterrows():
        low, high = rate_ranges.get(row["productLine"], default_range)
        current_rate_mapping[row["id"]] = numpy.random.uniform(low, high)

    current_rates = numpy.array([current_rate_mapping[p] for p in tested_product_ids])

    df_test_results = pandas.DataFrame({
        "id": test_ids,
        "productId": tested_product_ids,
        "charge": product_charge_number,
        "date": test_date,
        "shouldRatePerMinute": should_rates,
        "currentRatePerMinute": current_rates,
    })

    return df_test_results

def save_rawdata(rawdata: pandas.DataFrame, filename: str):
    rawdata.to_csv(f"{OUT_DIR}/{filename}.csv", index=False)

if __name__ == "__main__":
    generate()