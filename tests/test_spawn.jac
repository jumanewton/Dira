node N {}
walker W {
    can run with N entry { print("Running"); }
}
with entry {
    n = spawn N();
    n ++> W();
}
