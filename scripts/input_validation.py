def validate_input(msg="Yes or no? ", valid_types={("y", "yes", "Yes"): True,
                                                  ("n", "no", "No"): False}):
    while True:
        answer = input(msg).strip()
        for keys, value in valid_types.items():
            if answer in keys:
                return value
        print("Invalid input, try again.")
