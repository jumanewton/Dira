node Person {
    has name: str;
}

with entry {
    p = Person(name="Alice");
    print(p.name);
}