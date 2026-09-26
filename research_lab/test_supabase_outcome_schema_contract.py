from research_lab.supabase_outcome_schema_contract import assess


def main():
    columns = [
        {"column_name": "id", "data_type": "bigint",
         "column_default": None, "is_identity": "YES",
         "identity_generation": "BY DEFAULT"},
        {"column_name": "opportunity_key", "data_type": "text"},
        {"column_name": "sold", "data_type": "boolean"},
        {"column_name": "days_to_outcome", "data_type": "integer"},
    ]
    assert assess(columns) == {"write_ready": True, "issues": []}
    columns[0]["is_identity"] = "NO"
    assert assess(columns) == {
        "write_ready": False, "issues": ["id_has_no_generation"]
    }
    columns[0]["column_default"] = "nextval('outcome_id_seq'::regclass)"
    assert assess(columns) == {"write_ready": True, "issues": []}
    print("Supabase outcome schema preflight: PASS")


if __name__ == "__main__":
    main()
