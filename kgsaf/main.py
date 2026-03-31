from kgsaf.jdex.jdex import JDEX


if __name__ == "__main__":
    jdex = JDEX.from_json("./test/test_data/config.json")
    jdex.run()

