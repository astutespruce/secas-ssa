import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import {
  Box,
  Button,
  Flex,
  Heading,
  Text,
  Divider,
  Grid,
  Paragraph,
} from 'theme-ui'
import { FormProvider, useForm } from 'react-hook-form'

import DropZone from './DropZone'

const UploadForm = ({ onReset, onSubmit }) => {
  const methods = useForm({
    mode: 'onBlur',
  })

  const {
    formState: { isValid },
    watch,
    setValue,
  } = methods

  const file = watch('file', null)

  const handleSubmit = useCallback(
    (values) => {
      const { file: fileProp } = values

      onSubmit({ file: fileProp })
    },
    [onSubmit]
  )

  const handleResetFile = () => {
    setValue('file', null)
    onReset()
  }

  return (
    <>
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(handleSubmit)}>
          <Grid columns={[0, 2]} gap={5}>
            <Box>
              <Flex sx={{ alignItems: 'center', mb: '1rem' }}>
                <Box variant="boxes.step">1</Box>
                <Heading as="h3" sx={{ m: 0 }}>
                  Upload analysis unit boundaries
                </Heading>
              </Flex>
              <Paragraph>
                Upload a shapefile or ESRI File Geodatabase Feature Class with
                the boundaries of the analysis units you want to use for your
                report. Each analysis unit will be analyzed independently.
                <br />
                <br />
                You will be able to select the attribute that identifies the
                analysis units in the next step.
              </Paragraph>
            </Box>
            <Box>
              <Flex
                sx={{
                  mb: '0.5em',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <Box>
                  <Heading
                    as="h4"
                    sx={{
                      mb: 0,
                    }}
                  >
                    Analysis unit boundaries:
                  </Heading>
                  <Box>{file && <Text>{file.name}</Text>}</Box>
                </Box>
              </Flex>

              <Box sx={{ display: file ? 'none' : 'block' }}>
                <DropZone name="file" />
              </Box>

              <Divider />
              <Flex
                sx={{
                  justifyContent: 'space-between',
                }}
              >
                <Button
                  variant="secondary"
                  onClick={handleResetFile}
                  sx={{ visibility: file ? 'visible' : 'hidden' }}
                >
                  Choose a different file
                </Button>

                <Button
                  as="button"
                  type="submit"
                  variant={isValid ? 'primary' : 'disabled'}
                  disabled={!isValid}
                >
                  Upload file
                </Button>
              </Flex>
            </Box>
          </Grid>
        </form>
      </FormProvider>
    </>
  )
}

UploadForm.propTypes = {
  onReset: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default UploadForm
