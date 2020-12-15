import asyncio

from main_wingman import MainWingman
from wingman import Wingman

if __name__ == "__main__":
    extra_wingmen = []

    extra_wingmen.append(MainWingman(extra_wingmen))

    for i in range(1, 5):
        if i != 3:
            extra_wingmen.append(Wingman(i + 1))

    asyncio.get_event_loop().run_forever()
