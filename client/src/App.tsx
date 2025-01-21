import { Toaster } from "@/components/ui/toaster"
import { useState } from "react"
import { ChatInterface } from "./components/ChatInterface"
import { UploadModal } from "./components/uploadModal"
import { Sidebar } from "./components/Sidebar"

function App() {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false)
  const [documents, setDocuments] = useState<number[]>([])
  const [selectedDocument, setSelectedDocument] = useState<number | null>(null)

  // @ts-ignore
  const handleUpload = (fileName: string,document_id:number) => {
    setDocuments((prevDocs) => [...prevDocs, document_id])
    setSelectedDocument(document_id)
    setIsUploadModalOpen(false)
  }

  return (
    <Layout>
      <div className="flex h-screen">
          <Sidebar
            documents={documents}
            onUpload={() => setIsUploadModalOpen(true)}
            onSelectDocument={setSelectedDocument}
            selectedDocument={selectedDocument}
          />
          <ChatInterface selectedDocument={selectedDocument} />
          <UploadModal isOpen={isUploadModalOpen} onClose={() => setIsUploadModalOpen(false)} onUpload={handleUpload} />
      </div>
    </Layout>
  )
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      {children}
      <Toaster />
    </div>
  )
}

export default App;
