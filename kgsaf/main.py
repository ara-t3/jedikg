from kgsaf.jdex import JDEX


if __name__ == "__main__":
    jdex = JDEX.from_json("./kgsaf/data/configurations/WHOW_5_RON.json")
    jdex.run()

