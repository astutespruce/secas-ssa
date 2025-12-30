<script lang="ts">
	import { Root, Trigger, Content, Header, Title } from '$lib/components/ui/dialog'
	import { cn } from '$lib/utils'
	import { CONTACT_EMAIL } from '$lib/env'

	let { children, triggerClass = '' } = $props()
</script>

<Root>
	<Trigger class={cn(triggerClass)}>
		{@render children()}
	</Trigger>
	<Content class="pt-4 pb-6">
		<Header class="border-b pb-4 border-b-grey-3">
			<Title class="text-3xl">Contact us</Title>
		</Header>
		<p class="text-lg">
			Do you have a question about how to use this tool or interpret results? SSA Geospatial Toolkit
			staff are here to help!
			<br />
			<br />
			Please reach out to user support:
			<br />
			<br />
			<b>email</b>:
			<a
				href={`mailto:${CONTACT_EMAIL}?subject=SE Species Status Landscape Assessment Tool - user support`}
				target="_blank"
				rel="noopener noreferrer"
			>
				{CONTACT_EMAIL}
			</a>.
		</p>
	</Content>
</Root>
