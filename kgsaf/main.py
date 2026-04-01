from kgsaf.jdex import JDEX


if __name__ == "__main__":
    jdex = JDEX.from_json("./kgsaf/data/configurations/ARCO_5_ROFF.json")
    jdex.run()

