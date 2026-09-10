from backend.app.workflow import AuthorityWorkflow


def test_workflow_create_and_update(monkeypatch, tmp_path):
    import backend.app.workflow_storage as storage

    db = tmp_path / "workflow.db"
    monkeypatch.setattr(storage, "DB_PATH", db)

    # workflow imports the functions, whose globals still reference storage.DB_PATH.
    workflow = AuthorityWorkflow()
    item = workflow.create("pothole", 17.385, 78.486, 5, 0.94)
    workflow.update(item.id, "in_progress", assignee="GHMC", note="Crew dispatched")

    restored = AuthorityWorkflow()
    loaded = restored.items[item.id]
    assert loaded.status == "in_progress"
    assert loaded.assignee == "GHMC"
    assert "Crew dispatched" in loaded.notes
