import datetime

class Heat:

    bitmasks = [
            [b'0x01', b'0x02'],
            [b'0x04', b'0x08'],
            [b'0x10', b'0x20'],
            [b'0x40', b'0x80']
        ]
    nascar = 24.444444444444444444

    def __init__(self, dec=3):
        self.bit_times = []
        self.dec = dec
        self.err = False

    def add_bit_change(self, bit_change: str):
        """Append `bit_change` to `self.bit_times`
        `bit_change`: 'bit,miliseconds'"""

        self.bit_times.append(bit_change.strip())

    def get_results(self, lanes):
        """Calculates heat results & adds a 'run_data' key to each lane in `lanes` with the run data"""
        results = {}
        #print(self.bit_times)
        for lane, data in lanes.values():
            if not 'heatrun_id' in data:  # No car was racing, ignore data for this lane
                continue

            lane_bm = Heat.bitmasks[lane - 1]
            sec = self.get_lane_time(lane_bm)  # Get seconds from 1st sensor trigger to 2nd

            data['run_data'] = sec
            results[lane] = data

        return results

    # def get_results_old(self, lanes):
    #     """Calculates heat results & adds a 'run_data' key to each lane in `lanes` with the run data"""
    #     results = []
    #     #print(self.bit_times)
    #     for lane in lanes:
    #         if not 'car_id' in lane:  # No car was racing, ignore data for this lane
    #             continue

    #         lane_bm = Heat.bitmasks[lane.get('lane_number') - 1]
    #         #print(lane, lane_bm)
    #         sec = self.get_lane_time(lane_bm)  # Get seconds from 1st sensor trigger to 2nd
    #         dist = lane.get('sensor_distance', 24)
    #         #print(sec, dist)
    #         lane['run_data'] = self.get_lane_results(sec, dist)

    #         results.append(lane)

    #     return results

    # def get_lane_results(self, sec, dist):
    #     """Returns a dict of mph, fps, and mps results from `sec` and `dist`"""

    #     return {
    #         "mph": self.get_mph(sec, dist),
    #         "fps": self.get_fps(sec, dist),
    #         "mps": self.get_mps(sec, dist),
    #     }

    def get_lane_time(self, lane_masks) -> int:
        """For each sensor bitmask in `lane_masks`, find the first trigger in `self.bit_times`,
        then get the seconds difference between them.
        `lane_masks`: list of bitmasks in the form [lane_sensor1, lane_sensor2]"""
        times = []

        i = 0
        for bit_change in self.bit_times:

            [bit, micro_time] = bit_change.split(',')

            # print()
            # print(bit)
            # print("i < 2:", i < 2)
            # print("masks[i]:", int(lane_masks[i], 16))
            # print("int(bit):", int(bit, 2))
            # print("(masks[i] & int(bit)):", (int(lane_masks[i], 16) & int(bit, 2)))

            if i < 2 and (int(lane_masks[i], 16) & int(bit, 2)) > 0:
                times.append(int(micro_time))
                #print(times)
                i += 1

            if len(times) == 2:
                #print(times)
                t1, t2 = times
                tDiff = t2 - t1

                return datetime.timedelta(microseconds=tDiff).total_seconds()

        return 0

    # def get_mps(self, sec: int, inches: int) -> float:
    #     if sec == 0:
    #         return 0

    #     meters = inches / 39.37007874015748
    #     mps = meters / sec

    #     return float(f'{mps:.{self.dec}f}')


    # def get_mph(self, sec: int, inches: int) -> float:
    #     if sec == 0:
    #         return 0

    #     miles = (inches / 12) / 5280
    #     hours = sec / 3600
    #     mph = miles / hours * Heat.nascar

    #     return float(f"{mph:.{self.dec}f}")


    # def get_fps(self, sec: int, inches: int) -> float:
    #     if sec == 0:
    #         return 0

    #     feet = inches / 12
    #     fps = feet / sec

    #     return float(f"{fps:.{self.dec}f}")


