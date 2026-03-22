function Message({ role, text }) {
  return (
    <div style={{ margin: "10px 0" }}>
      <b>{role === "user" ? "You" : "AI"}:</b> {text}
    </div>
  );
}

export default Message;