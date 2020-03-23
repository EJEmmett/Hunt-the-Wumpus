from World import World


def main():
    world = World()

    while world.is_playing:
        world.print()
        world.process_environment()

        direction = input("Enter direction (n/s/w/e): ")
        if direction:
            direction = direction.lower().strip()[0]

            if direction in ['n', 's', 'w', 'e']:
                world.move(direction)
            else:
                print("Choose a valid direction.")

    print("Congrats you've won!" if world.has_won else "You lost.")
    world.print()
    world.print_model()


if __name__ == "__main__":
    main()
