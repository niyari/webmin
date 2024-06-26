#!/usr/local/bin/perl
# Display syscalls made by this process in real time

require './proc-lib.pl';
&ReadParse();
&ui_print_unbuffered_header(undef, $text{'trace_title'}, "", "trace");

%pinfo = &process_info($in{'pid'});
&can_edit_process($pinfo{'user'}) || &error($text{'edit_ecannot'});
if (!%pinfo) {
	print "<b>$text{'edit_gone'}</b> <p>\n";
	&ui_print_footer("", $text{'index_return'});
	exit;
	}

$syscalls = &ui_form_start("trace.cgi", "post")."\n".
	    &ui_hidden("pid", $in{'pid'})."\n".
	    "<b>$text{'trace_syscalls'}</b>\n".
	    &ui_radio("all", defined($in{'all'}) ? $in{'all'} : 1,
		      [ [ 1, $text{'trace_all'} ],
			[ 0, $text{'trace_sel'} ] ])."\n".
	    &ui_textbox("syscalls", $in{'syscalls'}, 40)."\n".
	    &ui_submit($text{'trace_change'})."\n".
	    &ui_form_end()."\n";

@syscalls = $in{'all'} ? ( ) : split(/\s+/, $in{'syscalls'});
$trace = &open_process_trace($in{'pid'},
			     \@syscalls);
$fmt = "%-8.8s %-11.11s %-80.80s %-10.10s";
print "<b>",&text('trace_start', "<tt>$pinfo{'args'}</tt>"),"</b><br>\n";
print $syscalls;
print "<pre>";
printf "$fmt\n", "Time", "System Call", "Parameters", "Return";
printf "$fmt\n", ("-"x8), ("-"x11), ("-"x80), ("-"x10);
while($action = &read_process_trace($trace)) {
	local $tm = strftime("%H:%M:%S", localtime($action->{'time'}));
	printf "$fmt\n", $tm, $action->{'call'},
			 join(", ", @{$action->{'args'}}),
			 $action->{'rv'};
	}
print "</pre>";
&close_process_trace($trace);
if (!kill(0, $in{'pid'})) {
	print "<b>$text{'trace_done'}</b><br>\n";
	}
else {
	print "<b>$text{'trace_failed'}</b><br>\n";
	}

&ui_print_footer("edit_proc.cgi?$in{'pid'}", $text{'edit_return'},
		 "", $text{'index_return'});

