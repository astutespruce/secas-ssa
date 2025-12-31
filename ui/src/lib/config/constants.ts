import datasetsJSON from '$constants/datasets.json'

import { indexBy } from '$lib/util/data'

const { categories: rawCategories, datasets: rawDatasets } = datasetsJSON

export const datasets = indexBy(rawDatasets, 'id')

export const categories = rawCategories.map(({ datasets: categoryDatasets, ...rest }) => ({
	...rest,
	datasets: categoryDatasets.map((id) => datasets[id])
}))
