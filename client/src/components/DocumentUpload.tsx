import { useState } from 'react'
import {
  Box,
  Button,
  Heading,
  Input,
  VStack,
  useToast,
  List,
  ListItem,
  Text,
} from '@chakra-ui/react'
import { FiUpload } from 'react-icons/fi'
import axios from 'axios'

const DocumentUpload = () => {
  const [files, setFiles] = useState<any[]>([])
  const [uploading, setUploading] = useState(false)
  const toast = useToast()

  const handleFileChange = (e:any) => {
    const selectedFiles = Array.from(e.target.files)
    setFiles(selectedFiles)
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      toast({
        title: 'No files selected',
        status: 'warning',
        duration: 3000,
      })
      return
    }

    setUploading(true)
    const formData = new FormData()
    files.forEach(file => {
      formData.append('file', file)
    })

    try {
      await axios.post('http://localhost:8000/api/documents/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      toast({
        title: 'Upload successful',
        status: 'success',
        duration: 3000,
      })
      setFiles([])
    } catch (error) {
      toast({
        title: 'Upload failed',
        // @ts-ignore
        description: error.message,
        status: 'error',
        duration: 3000,
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <Box w="full">
      <VStack spacing={4} align="stretch">
        <Heading size="md">Upload Documents</Heading>
        <Input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          multiple
        />
        {files.length > 0 && (
          <List spacing={2}>
            {files.map((file, index) => (
              <ListItem key={index}>
                <Text fontSize="sm">{file.name}</Text>
              </ListItem>
            ))}
          </List>
        )}
        <Button
          leftIcon={<FiUpload />}
          colorScheme="blue"
          onClick={handleUpload}
          isLoading={uploading}
        >
          Upload
        </Button>
      </VStack>
    </Box>
  )
}

export default DocumentUpload