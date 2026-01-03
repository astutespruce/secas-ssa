<script>
	import Envelope from '~icons/fa-solid/envelope'
	import ExclamationCircle from '~icons/fa-solid/ExclamationCircle'

	import { ContactDialog, ReportProblemDialog } from '$lib/components/dialog'
</script>

<footer
	class="hidden md:flex flex-none gap-4 items-center justify-between py-1 px-2 leading-none text-sm text-white bg-blue-9"
>
	<div class="flex flex-none gap-3 items-center">
		<div class="flex-none">
			<ContactDialog>
				<div class="flex items-center gap-2 cursor-pointer hover:underline">
					<Envelope class="size-4" aria-hidden="true" />
					Contact us
				</div>
			</ContactDialog>
		</div>
		<div class="hidden md:block">|</div>
		<div class="flex-none hidden md:block">
			<ReportProblemDialog>
				<div class="items-center gap-2 cursor-pointer hover:underline flex">
					<ExclamationCircle class="size-4" aria-hidden="true" />
					Report a problem
				</div>
			</ReportProblemDialog>
		</div>
		<div class="hidden lg:block">|</div>
	</div>

	<div class="text-right">
		Created by the
		<a href="https://www.fws.gov/" target="_blank" class="text-white no-underline">
			<span class="hidden xl:inline-block hover:underline">U.S. Fish and Wildlife Service</span>
			<span class="inline-block xl:hidden hover:underline">USFWS</span>
		</a>
		and
		<a
			href="https://astutespruce.com"
			target="_blank"
			class="text-white no-underline hover:underline">Astute Spruce</a
		>
	</div>
</footer>
