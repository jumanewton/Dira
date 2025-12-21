walker IntakeAgent {
    has report_data: dict;

    can validate_and_create with `root entry {
        # Placeholder: create report
    }
}

walker ClassifierAgent {
    has report_data: dict;
    has report: Report;

    can classify with Report entry {
        # Placeholder: classify
    }
}

walker DuplicateDetectorAgent {
    has report: Report;

    can detect with Report entry {
        # Placeholder: detect
    }
}

walker RouterAgent {
    has report: Report;

    can route with Report entry {
        # Placeholder: route
    }
}

with entry {
}