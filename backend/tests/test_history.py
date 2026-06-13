from src import db
from src.schema import ModuleConfig, TextInput


def _config(title: str) -> ModuleConfig:
    return ModuleConfig(title=title, components=[TextInput(id="a", label="A")])


def test_insert_records_initial_version():
    db.init_db()
    sid = db.ensure_session(None)
    m = db.insert_module(sid, _config("v1"))
    versions = db.list_versions(sid, m.id)
    assert len(versions) == 1
    assert versions[0].config.title == "v1"


def test_update_appends_version():
    db.init_db()
    sid = db.ensure_session(None)
    m = db.insert_module(sid, _config("v1"))
    db.update_module(sid, m.id, _config("v2"))
    versions = db.list_versions(sid, m.id)
    assert [v.config.title for v in versions] == ["v1", "v2"]


def test_update_skips_duplicate_versions():
    db.init_db()
    sid = db.ensure_session(None)
    m = db.insert_module(sid, _config("same"))
    db.update_module(sid, m.id, _config("same"))  # no-op save
    assert len(db.list_versions(sid, m.id)) == 1


def test_undo_reverts_to_previous_version():
    db.init_db()
    sid = db.ensure_session(None)
    m = db.insert_module(sid, _config("v1"))
    db.update_module(sid, m.id, _config("v2"))
    reverted = db.undo_module(sid, m.id)
    assert reverted is not None
    assert reverted.config.title == "v1"
    # And the live module reflects the revert.
    assert db.list_modules(sid)[0].config.title == "v1"


def test_undo_is_repeatable_walks_back_history():
    db.init_db()
    sid = db.ensure_session(None)
    m = db.insert_module(sid, _config("v1"))
    db.update_module(sid, m.id, _config("v2"))
    db.update_module(sid, m.id, _config("v3"))
    assert db.undo_module(sid, m.id).config.title == "v2"
    assert db.undo_module(sid, m.id).config.title == "v1"
    # Only the original version remains; nothing left to undo.
    assert db.undo_module(sid, m.id) is None


def test_undo_returns_none_when_single_version():
    db.init_db()
    sid = db.ensure_session(None)
    m = db.insert_module(sid, _config("only"))
    assert db.undo_module(sid, m.id) is None


def test_undo_is_scoped_to_session():
    db.init_db()
    s1 = db.ensure_session(None)
    s2 = db.ensure_session(None)
    m = db.insert_module(s1, _config("v1"))
    db.update_module(s1, m.id, _config("v2"))
    assert db.undo_module(s2, m.id) is None
    assert db.list_modules(s1)[0].config.title == "v2"  # untouched


def test_delete_clears_history():
    db.init_db()
    sid = db.ensure_session(None)
    m = db.insert_module(sid, _config("v1"))
    db.update_module(sid, m.id, _config("v2"))
    db.delete_module(sid, m.id)
    assert db.list_versions(sid, m.id) == []
