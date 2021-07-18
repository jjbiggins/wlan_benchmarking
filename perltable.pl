#!/usr/bin/perl
use warnings;
use strict;
use Perl6::Form;

my $student_data;

chomp( my $title = <DATA> );    

push @{$student_data}, [split] while <DATA>;

print "\n\nFIRST TABLE:\n";
print form
  "==============================================",
  "| STD_NAME | STD_NUM | SUB_A | SUB_B | SUB_C |",
  "==============================================";
print form
  "| {<<<<<<} |{||||||} | {||||}|{|||||}|{|||||}|",
  $_->[0], $_->[1], $_->[2], $_->[3], $_->[4]
  for @$student_data;

use Text::Table;
print "\n\nSECOND TABLE:\n";

my $plain_table = Text::Table->new( split /\s+/, $title );

$plain_table->load( [@$_] ) for @$student_data;

print $plain_table;
