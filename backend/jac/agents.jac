walker IntakeAgent {
    has report_data: dict;

    can validate_and_create with `root entry {
        print("IntakeAgent: validating and creating report");
        # Placeholder: create report
        print("Report created");
    }
}

walker ClassifierAgent {
    has report_data: dict;
    has report: Report;

    can classify with Report entry {
        print("ClassifierAgent: classifying report");
        # Placeholder: classify
        print("Report classified");
    }
}

walker DuplicateDetectorAgent {
    has report: Report;

    can detect with Report entry {
        print("DuplicateDetectorAgent: checking for duplicates");
        # Placeholder: detect
        print("Duplicates checked");
    }
}

walker RouterAgent {
    has report: Report;

    can route with Report entry {
        print("RouterAgent: routing report");
        # Placeholder: route
        print("Report routed");
    }
}

with entry {
    print("Agents loaded");
}