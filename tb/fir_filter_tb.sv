`timescale 1ns/1ps

module fir_filter_tb;

	localparam string INPUT_FILE = "sim/fir_input.txt";
	localparam string EXPECTED_FILE = "sim/fir_output.txt";
	localparam string ACTUAL_FILE = "sim/fir_hw_output.txt";
	localparam int CLK_PERIOD_NS = 10;

	logic clk;
	logic rst_n;
	logic valid_in;
	logic signed [15:0] data_in;
	logic valid_out;
	logic signed [15:0] data_out;

	int input_fd;
	int expected_fd;
	int actual_fd;
	int input_value;
	int expected_value;
	int scan_status;
	int sample_count;
	int output_count;
	int mismatch_count;

	int input_samples[$];
	int expected_samples[$];

	fir_filter dut (
		.clk(clk),
		.rst_n(rst_n),
		.valid_in(valid_in),
		.data_in(data_in),
		.valid_out(valid_out),
		.data_out(data_out)
	);

	initial clk = 1'b0;
	always #(CLK_PERIOD_NS / 2) clk = ~clk;

	initial begin
		$dumpfile("sim/fir_filter.vcd");
		$dumpvars(0, fir_filter_tb);

		input_fd = $fopen(INPUT_FILE, "r");
		if (input_fd == 0) begin
			$fatal(1, "Failed to open input file: %s", INPUT_FILE);
		end

		expected_fd = $fopen(EXPECTED_FILE, "r");
		if (expected_fd == 0) begin
			$fatal(1, "Failed to open expected file: %s", EXPECTED_FILE);
		end

		actual_fd = $fopen(ACTUAL_FILE, "w");
		if (actual_fd == 0) begin
			$fatal(1, "Failed to open output file: %s", ACTUAL_FILE);
		end

		sample_count = 0;
		scan_status = $fscanf(input_fd, "%d\n", input_value);
		while (scan_status == 1) begin
			input_samples.push_back(input_value);
			sample_count++;
			scan_status = $fscanf(input_fd, "%d\n", input_value);
		end

		scan_status = $fscanf(expected_fd, "%d\n", expected_value);
		while (scan_status == 1) begin
			expected_samples.push_back(expected_value);
			scan_status = $fscanf(expected_fd, "%d\n", expected_value);
		end

		if (expected_samples.size() != input_samples.size()) begin
			$fatal(1, "Input and expected sample counts differ: %0d vs %0d", input_samples.size(), expected_samples.size());
		end

		rst_n = 1'b0;
		valid_in = 1'b0;
		data_in = '0;

		repeat (2) @(posedge clk);
		rst_n = 1'b1;

		for (int idx = 0; idx < input_samples.size(); idx++) begin
			@(negedge clk);
			valid_in = 1'b1;
			data_in = input_samples[idx];
		end

		@(negedge clk);
		valid_in = 1'b0;
		data_in = '0;

		repeat (6) @(negedge clk);

		valid_in = 1'b0;
		data_in = '0;

		@(posedge clk);
		if (mismatch_count == 0) begin
			$display("FIR test completed successfully with %0d outputs.", output_count);
		end else begin
			$display("FIR test completed with %0d mismatches out of %0d outputs.", mismatch_count, output_count);
		end

		$fclose(input_fd);
		$fclose(expected_fd);
		$fclose(actual_fd);
		$finish;
	end

	always @(negedge clk or negedge rst_n) begin
		if (!rst_n) begin
			output_count <= 0;
			mismatch_count <= 0;
		end else if (valid_out) begin
			if (output_count < expected_samples.size()) begin
				if (int'(data_out) != expected_samples[output_count]) begin
					mismatch_count <= mismatch_count + 1;
					$display("Mismatch at output %0d: expected %0d got %0d", output_count, expected_samples[output_count], int'(data_out));
				end
				$fdisplay(actual_fd, "%0d", int'(data_out));
			end else begin
				mismatch_count <= mismatch_count + 1;
				$display("Unexpected extra output %0d: got %0d", output_count, int'(data_out));
				$fdisplay(actual_fd, "%0d", int'(data_out));
			end
			output_count <= output_count + 1;
		end
	end

endmodule
