/**
 * Convert an array to an object, indexing on values of field
 * @param {Array} records
 * @param {String} field
 */
export const indexBy = (records: { [key: string]: any }, field: string) =>
	records.reduce(
		(prev: {}, record: { [key: string]: any }) => Object.assign(prev, { [record[field]]: record }),
		{}
	)

	const numericRegex = /\d+/


