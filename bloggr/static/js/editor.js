import { Editor } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import Link from "@tiptap/extension-link";
import TextAlign from "@tiptap/extension-text-align";
import Placeholder from "@tiptap/extension-placeholder";

document.addEventListener("DOMContentLoaded", () => {
  const editors = [
    { id: "editor-new", contentField: "post_content" },
    { id: "editor-edit", contentField: "new_post_content" },
  ];

  editors.forEach(({ id, contentField }) => {
    const container = document.getElementById(id);
    if (!container) return;

    const editorContent = container.querySelector(".editor-content");
    const hiddenInput = container.querySelector(`[name="${contentField}"]`);

    const editor = new Editor({
      element: editorContent,
      extensions: [
        StarterKit.configure({
          heading: {
            levels: [1, 2, 3, 4, 5, 6],
          },
        }),
        Underline,
        Link.configure({
          openOnClick: false,
          HTMLAttributes: {
            class: "text-blue-600 underline",
          },
        }),
        TextAlign.configure({
          types: ["heading", "paragraph"],
        }),
        Placeholder.configure({
          placeholder: ({ node }) => {
            if (node.type.name === "paragraph" && node.nodeSize === 2) {
              return "Write your content here...";
            }
            return "";
          },
        }),
      ],
      content: hiddenInput?.value || "",
      editorProps: {
        attributes: {
          class: "prose prose-sm sm:prose lg:prose-lg max-w-none focus:outline-none",
        },
      },
      onUpdate: ({ editor }) => {
        if (hiddenInput) {
          hiddenInput.value = editor.getHTML();
        }
      },
    });

    const toolbar = container.querySelector(".editor-toolbar");
    if (!toolbar) return;

    toolbar.querySelectorAll("button, select").forEach((button) => {
      button.addEventListener("click", (e) => {
        e.preventDefault();
        const command = button.dataset.command;
        if (!command) return;

        switch (command) {
          case "bold":
            editor.chain().focus().toggleBold().run();
            break;
          case "italic":
            editor.chain().focus().toggleItalic().run();
            break;
          case "underline":
            editor.chain().focus().toggleUnderline().run();
            break;
          case "strike":
            editor.chain().focus().toggleStrike().run();
            break;
          case "code":
            editor.chain().focus().toggleCode().run();
            break;
          case "codeBlock":
            editor.chain().focus().toggleCodeBlock().run();
            break;

          case "heading":
            const level = parseInt(button.dataset.level || "1", 10);
            editor.chain().focus().toggleHeading({ level }).run();
            break;
          case "bulletList":
            editor.chain().focus().toggleBulletList().run();
            break;
          case "orderedList":
            editor.chain().focus().toggleOrderedList().run();
            break;
          case "blockquote":
            editor.chain().focus().toggleBlockquote().run();
            break;
          case "horizontalRule":
            editor.chain().focus().setHorizontalRule().run();
            break;
          case "link":
            const url = prompt("Enter URL:");
            if (url) {
              editor.chain().focus().setLink({ href: url }).run();
            }
            break;
          case "alignLeft":
            editor.chain().focus().setTextAlign("left").run();
            break;
          case "alignCenter":
            editor.chain().focus().setTextAlign("center").run();
            break;
          case "alignRight":
            editor.chain().focus().setTextAlign("right").run();
            break;
        }
      });
    });

    toolbar.querySelectorAll("select").forEach((select) => {
      select.addEventListener("change", (e) => {
        const command = select.dataset.command;
        const value = select.value;
        if (!command || !value) return;

        switch (command) {
          case "fontFamily":
            editor.chain().focus().setFontFamily(value).run();
            break;
          case "fontSize":
            editor.chain().focus().setMark("textStyle", { fontSize: value }).run();
            break;
        }
        select.value = "";
      });
    });
  });
});
