import React, { useEffect, useState } from "react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function TodoPage({ token, onLogout }) {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newTodo, setNewTodo] = useState("");
  const [editId, setEditId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [actionError, setActionError] = useState("");

  const fetchTodos = async () => {
    setLoading(true);
    setActionError("");
    const res = await fetch(`${BACKEND_URL}/todos/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) {
      const data = await res.json();
      setTodos(Array.isArray(data) ? data : []);
    } else if (res.status === 401 || res.status === 403) {
      setActionError("User can't perform this action");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (token) fetchTodos();
  }, [token]);

  const handleAdd = async (e) => {
    e.preventDefault();
    setActionError("");
    if (!newTodo) return;
    const res = await fetch(`${BACKEND_URL}/todos/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ title: newTodo })
    });
    if (res.ok) {
      setNewTodo("");
      fetchTodos();
    } else if (res.status === 401 || res.status === 403) {
      setActionError("User can't perform this action");
    }
  };

  const handleEdit = async (id) => {
    setActionError("");
    if (!editTitle) return;
    const res = await fetch(`${BACKEND_URL}/todos/${id}/`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ title: editTitle })
    });
    if (res.ok) {
      setEditId(null);
      setEditTitle("");
      fetchTodos();
    } else if (res.status === 401 || res.status === 403) {
      setActionError("User can't perform this action");
    }
  };

  const handleDelete = async (id) => {
    setActionError("");
    const res = await fetch(`${BACKEND_URL}/todos/${id}/`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) fetchTodos();
    else if (res.status === 401 || res.status === 403) {
      setActionError("User can't perform this action");
    }
  };

  if (!token) return <div>Please login to manage todos.</div>;
  if (loading) return <div>Loading todos...</div>;

  return (
    <div>
      <h2>Todos</h2>
      {actionError && <div style={{color: 'red'}}>{actionError}</div>}
      <form onSubmit={handleAdd}>
        <input
          type="text"
          placeholder="New todo"
          value={newTodo}
          onChange={e => setNewTodo(e.target.value)}
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {todos.map(todo => (
          <li key={todo.id || todo._id}>
            {editId === (todo.id || todo._id) ? (
              <>
                <input
                  type="text"
                  value={editTitle}
                  onChange={e => setEditTitle(e.target.value)}
                />
                <button onClick={() => handleEdit(todo.id || todo._id)}>Save</button>
                <button onClick={() => { setEditId(null); setEditTitle(""); }}>Cancel</button>
              </>
            ) : (
              <>
                {todo.title}
                <button onClick={() => { setEditId(todo.id || todo._id); setEditTitle(todo.title); }}>Edit</button>
                <button onClick={() => handleDelete(todo.id || todo._id)}>Delete</button>
              </>
            )}
          </li>
        ))}
      </ul>
      <button onClick={onLogout}>Logout</button>
    </div>
  );
}

export default TodoPage;
