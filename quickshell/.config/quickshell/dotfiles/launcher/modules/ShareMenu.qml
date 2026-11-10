Menu {
    label: "share"
    description: "Send text, files or folders with LocalSend"
    subtext: "Share"
    icon: "localsend"

    entries: [
        {
            name: "Send clipboard text",
            keywords: ["share", "localsend"],
            command: ["~/arch-desktop/bin/df-share", "clipboard"],
            scoped: false
        },
        {
            name: "Send files",
            keywords: ["share", "localsend"],
            command: ["~/arch-desktop/bin/df-share", "file"],
            scoped: false
        },
        {
            name: "Send folder",
            keywords: ["share", "localsend"],
            command: ["~/arch-desktop/bin/df-share", "folder"],
            scoped: false
        },
        {
            name: "Receive",
            keywords: ["share", "localsend"],
            command: ["~/arch-desktop/bin/df-share", "receive"],
            scoped: false
        }
    ]
}
