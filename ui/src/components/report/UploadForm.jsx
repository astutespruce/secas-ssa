import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import {
  Box,
  Button,
  Flex,
  Heading,
  Input,
  Text,
  Divider,
  Grid,
} from 'theme-ui'
import { FormProvider, useForm } from 'react-hook-form'

import DropZone from './DropZone'

const UploadForm = ({ onFileChange, onCreateReport }) => {
  const methods = useForm({
    mode: 'onBlur',
  })

  const {
    formState: { isValid },
    register,
    watch,
    setValue,
  } = methods

  const file = watch('file', null)

  const handleSubmit = useCallback(
    (values) => {
      const { areaName, file: fileProp } = values

      onCreateReport(fileProp, areaName)
    },
    [onCreateReport]
  )

  const handleResetFile = () => {
    setValue('file', null)
    onFileChange()
  }

  return (
    <>
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(handleSubmit)}>
          <Grid columns={[0, 2]} gap={5} sx={{ mt: '2rem' }}>
            <Box>
              <Heading as="h3" sx={{ mb: '0.5rem' }}>
                Area Name (optional):
              </Heading>
              <Input
                type="text"
                name="areaName"
                {...register('areaName', { required: false })}
              />

              <Flex
                sx={{
                  mt: '2rem',
                  mb: '0.5em',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <Heading
                    as="h3"
                    sx={{
                      mb: 0,
                    }}
                  >
                    Choose Area of Interest:
                  </Heading>
                  <div>{file && <Text>{file.name}</Text>}</div>
                </div>
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
                  Submit
                </Button>
              </Flex>
            </Box>

            <Text as="p">TODO: instructions</Text>
          </Grid>
        </form>
      </FormProvider>
    </>
  )
}

UploadForm.propTypes = {
  onFileChange: PropTypes.func.isRequired,
  onCreateReport: PropTypes.func.isRequired,
}

export default UploadForm
