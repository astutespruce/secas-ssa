import { graphql, useStaticQuery } from 'gatsby'
import { indexBy } from 'util/data'

export const useDatasets = () => {
  const {
    datasetsJson: { categories, datasets: datasetsArray },
  } = useStaticQuery(graphql`
    query datasetsQuery {
      datasetsJson {
        categories {
          id
          label
          color
          borderColor
          datasets
        }
        datasets {
          id
          name
          description
          methods
          url
          source
          date
          citation
          values {
            value
            label
          }
        }
      }
    }
  `)

  const datasets = indexBy(datasetsArray, 'id')

  return {
    categories: categories.map(({ datasets: categoryDatasets, ...rest }) => ({
      ...rest,
      datasets: categoryDatasets.map((id) => datasets[id]),
    })),
    datasets,
  }
}
