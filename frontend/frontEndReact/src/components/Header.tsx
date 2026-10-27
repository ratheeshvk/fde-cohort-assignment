interface HeaderProps {
    title: string;
    username: string;
    onLogout: () => void;
}

export default function Header({ title, username, onLogout }: HeaderProps) {
    return (
        <header className="app-header">
            <h1>{title}</h1>
            <div className="user-menu">
                <span>Signed in as <strong>{username}</strong></span>
                <button type="button" onClick={onLogout}>
                    Logout
                </button>
            </div>
        </header>
    );
}
