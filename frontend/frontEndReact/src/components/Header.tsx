interface HeaderProps {
    title: string;
}

export default function Header({ title }: HeaderProps) {
    return (
        <header>
            <h1>{title}</h1>
        </header>
    );
}   