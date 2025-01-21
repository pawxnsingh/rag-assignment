import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

interface SidebarProps {
  documents: number[];
  onUpload: () => void;
  onSelectDocument: (document: number) => void;
  selectedDocument: number | null;
}

export function Sidebar({
  documents,
  onUpload,
  onSelectDocument,
  selectedDocument,
}: SidebarProps) {
  return (
    <div className="w-64 bg-gray-100 p-4 flex flex-col">
      <h2 className="text-xl font-bold mb-4">Documents</h2>
      <Button onClick={onUpload} className="mb-4">
        Upload PDF
      </Button>
      <ScrollArea className="flex-grow">
        <ul className="space-y-2">
          {documents.map((doc, index) => (
            <li key={index}>
              <Button
                variant={doc === selectedDocument ? "secondary" : "ghost"}
                className="w-full justify-start"
                onClick={() => {
                  onSelectDocument(doc);
                  console.log(selectedDocument);
                }}
              >
                PDF no. {doc}
              </Button>
            </li>
          ))}
        </ul>
      </ScrollArea>
    </div>
  );
}
